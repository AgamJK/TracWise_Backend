import { SignIn } from '@clerk/clerk-react'

const SignInPage = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Welcome Back</h1>
          <p className="text-gray-600 mt-2">Sign in to your account</p>
        </div>
        <SignIn 
          routing="path" 
          path="/sign-in" 
          redirectUrl="/chat"
          signUpUrl="/sign-up"
        />
      </div>
    </div>
  )
}

export default SignInPage
